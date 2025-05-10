public class CNPJService
{
    private readonly string connString;
    
    public async Task<bool> ValidarCNPJ(long cnpj)
    {
        using (var conn = new SqlConnection(connString))
        {
            var cmd = new SqlCommand(
                "SELECT 1 FROM empresas WHERE cnpj_numerico = @cnpj", conn);
            cmd.Parameters.AddWithValue("@cnpj", cnpj);
            
            var result = await cmd.ExecuteScalarAsync();
            return result != null;
        }
    }
    
    public async Task<IEnumerable<long>> ListarFiliais(long cnpjMatriz)
    {
        using (var conn = new SqlConnection(connString))
        {
            var cmd = new SqlCommand(
                @"SELECT cnpj_numerico 
                  FROM empresas 
                  WHERE cnpj_numerico / 10000 = @matriz / 10000", conn);
            cmd.Parameters.AddWithValue("@matriz", cnpjMatriz);
            
            var filiais = new List<long>();
            using (var reader = await cmd.ExecuteReaderAsync())
            {
                while (await reader.ReadAsync())
                {
                    filiais.Add(reader.GetInt64(0));
                }
            }
            return filiais;
        }
    }
}
